import os
import json
import hashlib
import secrets

def hash_with_salt(password: str,
                   salt: bytes | None = None,
                   salt_bytes: int = 32,
                   algo: str = 'sha256') -> str:
    """
    对密码进行加盐哈希。
    参数
    ----
    password : str
        明文密码
    salt : bytes | None
        外部指定的盐；为 None 时自动生成随机盐
    salt_bytes : int
        自动生成盐的字节长度（默认 32 字节 = 256 位）
    algo : str
        哈希算法，支持 'sha256' / 'sha512' / 'blake2b' 等（需 hashlib 支持）

    返回
    ----
    str
        格式：salt$digest
        其中 salt 为十六进制字符串，digest 为对应算法的十六进制摘要
    """
    if salt is None:
        salt = secrets.token_bytes(salt_bytes)

    # 选择哈希算法
    try:
        hasher = hashlib.new(algo)
    except ValueError as e:
        raise ValueError(f"不支持的哈希算法: {algo}") from e

    # 盐 + 密码 组合后做哈希
    hasher.update(salt)
    hasher.update(password.encode('utf-8'))
    digest = hasher.hexdigest()

    # 返回 “十六进制盐 $ 十六进制摘要”
    return f"{salt.hex()}${digest}"


def verify_password(password: str, stored: str, algo: str = 'sha256') -> bool:
    """
    验证密码是否与存储的加盐哈希值匹配。
    stored 格式必须与 hash_with_salt 返回的格式一致：salt$digest
    """
    try:
        salt_hex, expected_digest = stored.split('$', 1)
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False

    return hash_with_salt(password, salt=salt, algo=algo) == stored



        