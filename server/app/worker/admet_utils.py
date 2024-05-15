import numpy as np
from deepchem import deepchem
from rdkit.Chem import Descriptors, Lipinski, MolFromSmiles

from app.core.config import Settings

settings = Settings()
STATIC_DIRECTION = settings.ADMET_MODEL_FOLDER

maccskeys = deepchem.feat.MACCSKeysFingerprint()
circular = deepchem.feat.CircularFingerprint()
mol2vec = deepchem.feat.Mol2VecFingerprint(STATIC_DIRECTION + "/model_300dim.pkl")
mordred = deepchem.feat.MordredDescriptors(ignore_3D=True)
rdkit = deepchem.feat.RDKitDescriptors()
pubchem = deepchem.feat.PubChemFingerprint()


def featurize(smiles):
    """
    featurize SMILES into features
    """
    # featurize
    feat_maccskeys = maccskeys.featurize(smiles)
    feat_circular = circular.featurize(smiles)
    feat_mol2vec = mol2vec.featurize(smiles)
    feat_mordred = mordred.featurize(smiles)
    feat_rdkit = rdkit.featurize(smiles)
    feat_pubchem = pubchem.featurize(smiles)

    # process pubchem empty lists
    if len(feat_pubchem) != 881:
        feat_pubchem = np.array([0] * 881).reshape(1, 881)

    features = np.concatenate(
        (
            feat_maccskeys,
            feat_circular,
            feat_mol2vec,
            feat_mordred,
            feat_rdkit,
            feat_pubchem,
        ),
        axis=1,
    )

    return features


def properties(smiles):
    """
    calculate molecular properties
    """
    mol = MolFromSmiles(smiles)
    numHAcceptors = Lipinski.NumHAcceptors(mol)
    numHDonors = Lipinski.NumHDonors(mol)
    logp = Descriptors.MolLogP(mol)
    weight = Descriptors.ExactMolWt(mol)
    heter = Descriptors.NumHeteroatoms(mol)
    rot = Descriptors.NumRotatableBonds(mol)
    ring = Descriptors.RingCount(mol)

    # post-processing
    weight = round(weight, 2)
    logp = round(logp, 2)

    return (numHAcceptors, numHDonors, logp, weight, heter, rot, ring)


def get_colors(results):
    # green, yellow, red
    color_code = ["#D5F5E3", "#FCF3CF", "#FADBD8"]

    # Molecule Properties
    results["weight_color"] = (
        color_code[0]
        if (results["weight"] >= 100 and results["weight"] <= 600)
        else color_code[2]
    )

    results["heter_color"] = (
        color_code[0]
        if (results["heter"] >= 1 and results["heter"] <= 15)
        else color_code[2]
    )

    results["rot_color"] = color_code[0] if (results["rot"] <= 11) else color_code[2]

    results["ring_color"] = color_code[0] if (results["ring"] <= 6) else color_code[2]

    results["numHAcceptors_color"] = (
        color_code[0] if (results["numHAcceptors"] <= 12) else color_code[2]
    )

    results["numHDonors_color"] = (
        color_code[0] if (results["numHDonors"] <= 7) else color_code[2]
    )

    results["logp_color"] = (
        color_code[0]
        if (results["logp"] >= 0 and results["logp"] <= 3)
        else color_code[2]
    )

    # Absorption
    results["caco2_color"] = (
        color_code[0] if (results["caco2_wang"] >= -5.15) else color_code[2]
    )

    results["hia_color"] = (
        color_code[2]
        if (results["hia_hou"] <= 30)
        else color_code[1]
        if results["hia_hou"] <= 80
        else color_code[0]
    )

    results["pgp_color"] = (
        color_code[0]
        if (results["pgp_broccatelli"] <= 30)
        else color_code[1]
        if results["pgp_broccatelli"] <= 70
        else color_code[2]
    )

    results["lipo_color"] = (
        color_code[0]
        if (
            results["lipophilicity_astrazeneca"] >= 1
            and results["lipophilicity_astrazeneca"] <= 3
        )
        else color_code[2]
    )

    results["aqsol_color"] = (
        color_code[0]
        if (results["solubility_aqsoldb"] >= -2)
        else color_code[1]
        if results["solubility_aqsoldb"] >= -4
        else color_code[2]
    )

    results["bbb_color"] = (
        color_code[0]
        if (results["bbb_martins"] <= 30)
        else color_code[1]
        if results["bbb_martins"] <= 70
        else color_code[2]
    )

    results["ppbr_color"] = (
        color_code[0] if (results["pgp_broccatelli"] <= 90) else color_code[2]
    )

    results["vdss_color"] = (
        color_code[0]
        if (results["vdss_lombardo"] >= 0.04 and results["vdss_lombardo"] <= 20)
        else color_code[2]
    )

    results["herg_color"] = (
        color_code[0]
        if (results["herg"] <= 30)
        else color_code[1]
        if results["herg"] <= 70
        else color_code[2]
    )

    results["ames_color"] = (
        color_code[0]
        if (results["ames"] <= 30)
        else color_code[1]
        if results["ames"] <= 70
        else color_code[2]
    )

    results["dili_color"] = (
        color_code[0]
        if (results["dili"] <= 30)
        else color_code[1]
        if results["dili"] <= 70
        else color_code[2]
    )

    return results


def correct_encoding(dictionary):
    """Correct the encoding of python dictionaries so they can be encoded to mongodb
    inputs
    -------
    dictionary : dictionary instance to add as document
    output
    -------
    new : new dictionary with (hopefully) corrected encodings"""

    new = {}
    for key1, val1 in dictionary.items():
        # Nested dictionaries
        if isinstance(val1, dict):
            val1 = correct_encoding(val1)

        if isinstance(val1, np.bool_):
            val1 = bool(val1)

        if isinstance(val1, np.integer):
            val1 = int(val1)

        if isinstance(val1, np.floating):
            val1 = float(val1)

        new[key1] = val1

    return new
