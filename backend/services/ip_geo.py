"""
计算机修行录 - IP 属地解析服务
ip-api.com 为主（服务器实测可访问），太平洋IP为备用，内存缓存。
"""
import ipaddress

import requests

_cache: dict[str, str] = {}


def _is_private_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except ValueError:
        return True


def get_ip_province(ip: str) -> str:
    """根据 IP 获取属地，失败返回空字符串。"""
    if not ip or ip == "unknown":
        return ""

    if ip in _cache:
        return _cache[ip]

    if _is_private_ip(ip):
        _cache[ip] = "本地"
        return "本地"

    # 先试 ip-api.com（服务器实测可用）
    result = _try_ipapi(ip)
    if not result:
        # 备用：太平洋IP（国内服务）
        result = _try_pconline(ip)

    _cache[ip] = result
    return result


def _try_ipapi(ip: str) -> str:
    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "country,regionName,city"},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") != "fail":
                region = data.get("regionName", "")
                city = data.get("city", "")
                country = data.get("country", "")
                # 国内IP优先显示城市，国外显示国家
                if country == "China":
                    if city:
                        return city
                    return region or "中国"
                else:
                    if region:
                        return region
                    return country
    except Exception:
        pass
    return ""


def _try_pconline(ip: str) -> str:
    try:
        resp = requests.get(
            "https://whois.pconline.com.cn/ipJson.jsp",
            params={"ip": ip, "json": "true"},
            timeout=5,
        )
        if resp.status_code == 200:
            resp.encoding = "utf-8"
            data = resp.json()
            pro = data.get("pro", "")
            city = data.get("city", "")
            if pro:
                return pro + (" " + city if city and city != pro else "")
    except Exception:
        pass
    return ""
