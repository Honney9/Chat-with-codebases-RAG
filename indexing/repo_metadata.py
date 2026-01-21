from pymongo import MongoClient
import os

def is_repo_already_indexed(repo_id, commit_hash):
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["code_rag"]
    meta = db["repo_metadata"]

    return meta.find_one({
        "repo_id": repo_id,
        "commit_hash": commit_hash
    }) is not None


def mark_repo_as_indexed(repo_id, commit_hash):
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["code_rag"]
    meta = db["repo_metadata"]

    meta.update_one(
        {"repo_id": repo_id},
        {"$set": {"commit_hash": commit_hash}},
        upsert=True
    )
