from app.core.config import Settings
from aiobotocore.session import get_session


settings = Settings()


s3_session = get_session()

async def create_presigned_url(client, key):
    return await client.generate_presigned_url('get_object',Params={'Bucket': settings.S3_BUCKET_NAME,
                            'Key': key},
                            ExpiresIn=604700)
