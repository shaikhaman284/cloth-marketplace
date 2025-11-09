import requests
import json

BASE_URL = "https://api.awm27.shop"  # Change to your URL


def check_endpoint(method, endpoint, data=None, headers=None):
    """Test an endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)

        status = "✅" if response.status_code in [200, 201] else "❌"
        print(f"{status} {method} {endpoint} - {response.status_code}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False


print("=" * 50)
print("🔍 Production Health Check")
print("=" * 50)

# Test public endpoints
print("\n📋 Public Endpoints:")
check_endpoint("GET", "/api/categories")
check_endpoint("GET", "/api/products")
check_endpoint("GET", "/api/shops/approved")

# Test protected endpoints (will fail without token, but should return 401)
print("\n🔒 Protected Endpoints:")
response = requests.get(f"{BASE_URL}/api/orders/my-orders")
status = "✅" if response.status_code == 401 else "❌"
print(f"{status} GET /api/orders/my-orders - {response.status_code} (Expected 401)")

# Test admin
print("\n👨‍💼 Admin Panel:")
response = requests.get(f"{BASE_URL}/admin/")
status = "✅" if response.status_code == 200 else "❌"
print(f"{status} GET /admin/ - {response.status_code}")

# Test HTTPS
print("\n🔒 Security:")
if BASE_URL.startswith("https://"):
    print("✅ HTTPS enabled")
else:
    print("❌ HTTPS not enabled")

print("\n" + "=" * 50)
print("Health check complete!")
print("=" * 50)