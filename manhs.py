import requests
import base64
import os

def get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

def create_repo(token, repo_name):
    url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "description": "Repo được tạo tự động",
        "private": False
    }
    response = requests.post(url, headers=get_headers(token), json=data)
    if response.status_code == 201:
        print(f"Tạo repo '{repo_name}' thành công.")
    else:
        print("Lỗi khi tạo repo:", response.json())
        exit()

def upload_file(token, username, repo_name, file_path, dest_path):
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{dest_path}"
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    data = {
        "message": f"Add {dest_path}",
        "content": content
    }
    response = requests.put(url, headers=get_headers(token), json=data)
    if response.status_code in [201, 200]:
        print(f"✅ Tải file {dest_path} lên thành công.")
    else:
        print("❌ Lỗi khi tải file:", response.json())
        exit()

def get_raw_url(username, repo_name, file_path):
    return f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{file_path}"

def main():
    print("=== Tool Upload File lên GitHub và Lấy Link Raw ===")
    
    token = input("🔑 Nhập GitHub Personal Access Token (PAT): ").strip()
    
    # Xác thực và lấy username
    user_resp = requests.get("https://api.github.com/user", headers=get_headers(token))
    if user_resp.status_code != 200:
        print("❌ Token không hợp lệ.")
        return
    username = user_resp.json()["login"]
    print(f"✅ Xác thực thành công. Tài khoản: {username}")

    repo_name = input("📦 Nhập tên repo muốn tạo: ").strip()
    create_repo(token, repo_name)

    # Tạo README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# {repo_name}\nRepo được tạo tự động.")

    upload_file(token, username, repo_name, "README.md", "README.md")

    choice = input("📄 Bạn muốn:\n1. Upload file có sẵn\n2. Tạo file mới\nChọn (1/2): ")
    if choice == "1":
        file_path = input("📂 Nhập đường dẫn file muốn upload: ").strip()
        dest_name = os.path.basename(file_path)
        upload_file(token, username, repo_name, file_path, dest_name)
        print("🔗 Link RAW của file:", get_raw_url(username, repo_name, dest_name))
    elif choice == "2":
        filename = input("📝 Nhập tên file muốn tạo (VD: code.txt): ").strip()
        content = input("💬 Nhập nội dung file: ")
        # Tạo file tạm
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        upload_file(token, username, repo_name, filename, filename)
        print("🔗 Link RAW của file:", get_raw_url(username, repo_name, filename))
        os.remove(filename)
    else:
        print("❌ Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    main()
