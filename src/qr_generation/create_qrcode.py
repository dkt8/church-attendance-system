import csv
import os
import overlay_images
import qrcode

# Define the output directory
target = 'nghia3' 
os.makedirs(target, exist_ok=True)

# Read children data from kids.csv
children = {}
with open(f'{target}.csv', mode='r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip the header row
    for index, row in enumerate(csv_reader):
        #if 8 < index: #<= 70:
            #child_id = row[0]
        child_id = index
        name = f"{row[1]} {row[2]} {row[3]}".replace('\xa0', '').strip()
        #name = f"{row[0]} {row[1]} {row[2]}".replace('\xa0', '').strip()
        
        if name:  # Check if the name is not empty
            #children[int(child_id)] = name
            qr = qrcode.make(str(name))
            qr.save(os.path.join(target, f"{name}_QR.png"))

            qr_filename = f"{name}_QR.png"
            qr_filepath = os.path.join(target, qr_filename)
            qr = qrcode.make(str(name))
            qr.save(qr_filepath)

            #overlay_path = qr_filepath  # Use the saved QR code file as the overlay
            #saint_name = row[0]
            #full_name = f"{row[1]} {row[2]}".replace('\xa0', ' ').strip()
            #print(full_name)
            #x_position = 800  # Assign custom X position
            #y_position = 300  # Assign custom Y position

            #output_name = f"{name}_card.png"
            #overlay_images.overlay_images(target, output_name, overlay_path, saint_name, full_name, x_position, y_position)


#print(children)
# {1: 'Louis Nguyễn Trần Trường An', 
#  2: 'Maria Phan Vũ Thiên An', 
#  3: 'Maria Lưu Hoàng Mai Anh'}

#Generate QR codes for each child
# for child_id, name in children.items():
#     qr = qrcode.make(str(name))
#     qr.save(os.path.join(target, f"{name}_QR.png"))

#qr = qrcode.make("Đa Minh Phan Thiên Phú")
#qr.save(os.path.join(target, f"{"Đa Minh Phan Thiên Phú"}_QR.png"))

print("QR codes generated successfully!")

