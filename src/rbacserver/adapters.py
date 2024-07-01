import casbin
from casbin import Adapter, load_policy_line, AsyncEnforcer
from casbin.persist.adapters.asyncio import AsyncAdapter
from casbin.util import regex_match_func
from loguru import logger
from odmantic import AIOEngine

from src.components import datamodels
from src.components.config import APIServerConfig
from src.components.utils import get_async_mongo_db_connection

from .defaults import system_config_text


def get_text_policy_iterator(text):
    for line in text.split("\n"):
        p = list(map(
            lambda x: x.strip(), line.split(", ")
        ))
        if len(p) > 1:
            yield p
        else:
            continue


class MemoryAdapter(Adapter):
    """The memory adapter for Casbin.
    It can load policy from a string or save policy in memory.
    """

    _policy_data = ""

    def __init__(self, policy_data):
        self._policy_data = policy_data

    def load_policy(self, model):
        if not self._policy_data:
            raise RuntimeError("Invalid policy data, policy data cannot be empty")

        self._load_policy_data(model)

    def save_policy(self, model):
        self._policy_data = self._save_policy_data(model)

    def _load_policy_data(self, model):
        lines = self._policy_data.split("\n")
        for line in lines:
            load_policy_line(line.strip(), model)

    def _save_policy_data(self, model):
        lines = []

        if "p" in model.model.keys():
            for key, ast in model.model["p"].items():
                for pvals in ast.policies:
                    lines.append(key + ", " + ", ".join(pvals))

        if "g" in model.model.keys():
            for key, ast in model.model["g"].items():
                for pvals in ast.policies:
                    lines.append(key + ", " + ", ".join(pvals))

        policy_data = "\n".join(lines)
        return policy_data

    def add_policy(self, sec, ptype, rule):
        pass

    def add_policies(self, sec, ptype, rules):
        pass

    def remove_policy(self, sec, ptype, rule):
        pass

    def remove_policies(self, sec, ptype, rules):
        pass


class AsyncMemoryAdapter(AsyncAdapter):
    """the async memory adapter for Casbin.
    It can load policy from a text string or save policy to a text string.
    """

    _policy_data = ""

    def __init__(self, policy_text):
        self._policy_data = policy_text

    async def load_policy(self, model):
        if not self._policy_data:
            raise RuntimeError("invalid policy text, policy text cannot be empty")

        self._load_policy_text(model)

    async def save_policy(self, model):
        self._save_policy_text(model)

    def _load_policy_text(self, model):
        lines = self._policy_data.split("\n")
        for line in lines:
            load_policy_line(line.strip(), model)

    def _save_policy_text(self, model):
        lines = []

        if "p" in model.model.keys():
            for key, ast in model.model["p"].items():
                for pvals in ast.policies:
                    lines.append(key + ", " + ", ".join(pvals))

        if "g" in model.model.keys():
            for key, ast in model.model["g"].items():
                for pvals in ast.policies:
                    lines.append(key + ", " + ", ".join(pvals))

        for i, line in enumerate(lines):
            if i != len(lines) - 1:
                lines[i] += "\n"

        self._policy_data = "".join(lines)

    async def add_policy(self, sec, ptype, rule):
        pass

    async def add_policies(self, sec, ptype, rules):
        pass

    async def remove_policy(self, sec, ptype, rule):
        pass

    async def remove_policies(self, sec, ptype, rules):
        pass

    async def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        pass


class AsyncMongoDBAdapter(AsyncAdapter):
    """the async memory adapter for Casbin.
    It can load policy from a text string or save policy to a text string.
    """

    _engine: AIOEngine = None

    def __init__(self, mongo_engine: AIOEngine):
        self._engine = mongo_engine

    async def load_policy(self, model):
        await self._load_policy_db(model)

    async def save_policy(self, model):
        self._save_policy_db(model)

    async def _load_policy_db(self, model):
        policies = await self._engine.find(datamodels.RBACPolicyModelV2, {"policies": {"$exists": True}})
        if len(policies) == 0:
            logger.warning("no policy found in the database")
        else:
            logger.info(f"loading {len(policies)} policies from the database")

        for policy in policies:
            for pvals in policy.policies:
                load_policy_line(", ".join(pvals), model)

    def _save_policy_db(self, model):
        """
        Policy data is saved to the database on each change.
        """
        pass

    async def add_policy(self, sec, ptype, rule):
        """
        Policy data will not add to the database, only in memory.
        """
        pass

    async def add_policies(self, sec, ptype, rules):
        """
        Policy data will not add to the database, only in memory.
        """
        pass

    async def remove_policy(self, sec, ptype, rule):
        """
        No way to remove policy from the database or memory, only reload can clear old policies
        """
        pass

    async def remove_policies(self, sec, ptype, rules):
        """
        No way to remove policy from the database or memory, only reload can clear old policies
        """
        pass

    async def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """
        No way to remove policy from the database or memory, only reload can clear old policies
        """
        pass


# def build_casbin_enforcer(opt: APIServerConfig) -> Enforcer:
#     model = casbin.Model()
#     model.load_model_from_text(system_config_text)
#     # adapter = AsyncMemoryAdapter(system_policy_text)
#     adapter = casbin_pymongo_adapter.Adapter(
#         get_db_uri(opt),
#         dbname=datamodels.database_name,
#         collection=datamodels.policy_collection_name
#     )
#     e = casbin.Enforcer(model, adapter)
#     e.add_named_matching_func("keyMatch", regex_match_func)
#     return e

def build_casbin_enforcer(opt: APIServerConfig) -> AsyncEnforcer:
    model = casbin.Model()
    model.load_model_from_text(system_config_text)
    engine = AIOEngine(client=get_async_mongo_db_connection(opt), database=datamodels.database_name)
    adapter = AsyncMongoDBAdapter(engine)
    e = casbin.AsyncEnforcer(model, adapter)
    e.add_named_matching_func("keyMatch", regex_match_func)
    return e
