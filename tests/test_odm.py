from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
import asyncio
from src.components.datamodels import UserModelV2, UserRoleEnum, QuotaModelV2

db = AsyncIOMotorClient("mongodb://clpl:clpl@127.0.0.1")
engine = AIOEngine(client=db, database="test_odmantic")


async def go():
    await engine.database.drop_collection("user")
    async for doc in engine.find(UserModelV2):
        print(doc)
    await engine.configure_database([UserModelV2], update_existing_indexes=True)

    # create an user and insert it into mongodb
    user = UserModelV2(username="admin", role=UserRoleEnum.admin, password="admin")
    print(user.username, user.uuid)
    await engine.save(user)

    # retrieve the object from mongodb
    user = await engine.find_one(UserModelV2, UserModelV2.username == "admin")
    print(user.username, user.uuid)  # Outputs: admin

    # try to insert the same user again
    user = UserModelV2(username="admin2", role=UserRoleEnum.admin, password="admin")
    try:
        await engine.save(user)
    except Exception as e:
        print(e)

    user = UserModelV2(username="user", role=UserRoleEnum.user, password="user")
    await engine.save(user)
    print(user.username, user.uuid)

    # user = UserModelV2(username="user", role=UserRoleEnum.user, password="user", quota=QuotaModelV2())
    # await engine.save(user)


loop = asyncio.get_event_loop()
loop.run_until_complete(go())
