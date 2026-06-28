"""
计算机修行录 - IP 属地解析服务
使用 ip-api.com 免费 API，内存缓存。
"""
import ipaddress
from typing import Optional

import requests

# 内存缓存：{ip_str: province_str}
_cache: dict[str, str] = {}


def _is_private_ip(ip: str) -> bool:
    """判断是否为内网/本地 IP。"""
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except ValueError:
        return True  # 非法 IP 也当作本地处理


def get_ip_province(ip: str) -> str:
    """根据 IP 获取省份（如"广东省"），失败返回空字符串。"""
    if not ip or ip == "unknown":
        return ""

    if ip in _cache:
        return _cache[ip]

    if _is_private_ip(ip):
        _cache[ip] = "本地"
        return "本地"

    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "country,regionName", "lang": "zh-CN"},
            timeout=3,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") != "fail":
                region = data.get("regionName", "")
                country = data.get("country", "")
                if region:
                    # 直辖市 regionName 就是城市名，返回即可
                    result = region
                elif country:
                    result = country
                else:
                    result = ""
                _cache[ip] = result
                return result
    except (requests.RequestException, ValueError):
        pass

    _cache[ip] = ""
    return ""
