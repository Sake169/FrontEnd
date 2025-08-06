import urllib.request
import urllib.parse
import json

def test_login():
    url = "http://localhost:8001/api/v1/auth/login"
    data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        print(f"Testing login at: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        # 准备请求数据
        json_data = json.dumps(data).encode('utf-8')
        
        # 创建请求
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # 发送请求
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_text = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            print(f"Response Text: {response_text}")
            
            if status_code == 200:
                print("✅ Login successful!")
                return json.loads(response_text)
            else:
                print(f"❌ Login failed with status {status_code}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return None

if __name__ == "__main__":
    test_login()