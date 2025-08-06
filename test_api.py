#!/usr/bin/env python3
import requests
import json

# 登录获取token
login_url = "http://localhost:8001/api/v1/auth/login"
login_data = {
    "username": "demo",
    "password": "demo123"
}

print("正在登录...")
response = requests.post(login_url, json=login_data)
print(f"登录响应状态: {response.status_code}")
print(f"登录响应内容: {response.text}")

if response.status_code == 200:
    login_result = response.json()
    token = login_result.get('access_token')
    print(f"获取到token: {token[:50]}...")
    
    # 测试family-members接口
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    family_url = "http://localhost:8001/api/v1/family-members/"
    print(f"\n正在访问: {family_url}")
    family_response = requests.get(family_url, headers=headers)
    print(f"family-members响应状态: {family_response.status_code}")
    print(f"family-members响应内容: {family_response.text}")
else:
    print("登录失败")