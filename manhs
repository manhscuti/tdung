import os, base64, bz2, zlib, lzma, marshal, hashlib, secrets
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import HMAC, SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def manhs_generate_keys():
    if not os.path.exists("private.pem") or not os.path.exists("public.pem"):
        key = RSA.generate(2048)
        with open("private.pem", "wb") as f:
            f.write(key.export_key())
        with open("public.pem", "wb") as f:
            f.write(key.publickey().export_key())

def manhs_encrypt_file(input_file, output_file):
    # Bước 1: Random key, salt, iv
    key = secrets.token_bytes(32)
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)

    # Bước 2: Dẫn xuất khoá bằng PBKDF2 + SHA512
    derived_key = PBKDF2(key, salt, dkLen=32, count=100000, hmac_hash_module=SHA512)
    derived_iv = PBKDF2(iv, salt, dkLen=12, count=100000, hmac_hash_module=SHA512)

    # Bước 3: AES-GCM mã hóa nội dung file
    with open(input_file, "rb") as f:
        data = f.read()
    cipher = AES.new(derived_key, AES.MODE_GCM, nonce=derived_iv)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    # Bước 4: HMAC để xác thực
    hmac = HMAC.new(derived_key, ciphertext, SHA512).digest()

    # Bước 5: RSA mã hóa khoá
    with open("public.pem", "rb") as f:
        pubkey = RSA.import_key(f.read())
    rsa_cipher = PKCS1_OAEP.new(pubkey)
    enc_key = rsa_cipher.encrypt(key)

    # Bước 6: XOR kết quả
    def xor_bytes(data, key):
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

    xor_data = xor_bytes(ciphertext + tag + hmac, salt)

    # Bước 7: Ghi file tạm
    temp_file = "manhs_output"
    with open(temp_file, "wb") as f:
        f.write(base64.b64encode(enc_key + salt + iv + xor_data))

    # Bước 8: Lớp nén và mã hóa tiếp theo
    with open(temp_file, "rb") as f:
        raw = f.read()

    compressed = marshal.dumps(lzma.compress(zlib.compress(bz2.compress(base64.b85encode(raw)))))
    hexed = compressed.hex().encode()
    final_data = base64.b64encode(xor_bytes(hexed, b"manhs_secret_key"))

    # Bước 9: Ghi file output + mã hoá import + gắn public key
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#Copyright by MinhAnhs.\n")
        f.write("exec(__import__('base64').b64decode(b'''\\\n")
        f.write(base64.b64encode(f'''
import base64, marshal, bz2, zlib, lzma

def manhs_decrypt():
    def xor_bytes(data, key):
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    enc_data = {repr(final_data)}
    data = xor_bytes(base64.b64decode(enc_data), b"manhs_secret_key")
    data = marshal.loads(bytes.fromhex(data.decode()))
    data = base64.b85decode(bz2.decompress(zlib.decompress(lzma.decompress(data))))
    # Bạn cần viết thêm mã giải mã sâu hơn nếu cần chạy mã gốc.

manhs_decrypt()
'''.strip().encode()).decode())
        f.write("'''))")

    # Xoá các file tạm và khóa
    os.remove("private.pem")
    os.remove("public.pem")
    os.remove(temp_file)

# === Chạy tool chính ===
if __name__ == "__main__":
    inp = input("Nhập tên file đầu vào (VD: file.py): ")
    outp = input("Nhập tên file đầu ra (VD: file_out.py): ")

    if not os.path.exists(inp):
        print("Không tìm thấy file đầu vào.")
        exit(1)

    manhs_generate_keys()
    manhs_encrypt_file(inp, outp)
    print("Đã mã hóa xong và tạo file:", outp)
