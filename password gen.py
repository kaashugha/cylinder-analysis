import bcrypt

password = "abc".encode('utf-8')
hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

print(password)
print(hash_password)