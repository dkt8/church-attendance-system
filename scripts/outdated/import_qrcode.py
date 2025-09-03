import qrcode

# Base URL of the Apps Script
# base_url = "https://script.google.com/macros/s/abc123/exec?id="
#base_url =   "https://script.google.com/macros/s/AKfycbzSbRSl60BJs9cUfnxaFYPK6Ds3hJZKvtKbrM1EXLdKKlvOS2lUobH9ayY9GO263u-KBA/exec?id="


# Example child data
children = {
    1: "Loc",
    2: "Hoai",
    3: "Duy",
    4: "Khanh",
    5: "Duc",
    6: "John"

}

for child_id, name in children.items():
    #qr = qrcode.make(base_url + str(child_id))
    qr = qrcode.make(str(child_id))
    qr.save(f"{name}_QR.png")
print("QR codes generated successfully!")
