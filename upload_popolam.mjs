import fs from 'fs';
const cloudName = 'dmzsczjzd';
const uploadPreset = 'kimmeria_unsigned';

async function upload(filePath, publicId) {
  const bytes = fs.readFileSync(filePath);
  const base64 = bytes.toString('base64');
  const dataUri = 'data:image/jpeg;base64,' + base64;
  const body = new FormData();
  body.append('file', dataUri);
  body.append('upload_preset', uploadPreset);
  body.append('folder', 'kimmeria/popolam');
  body.append('public_id', publicId);
  const res = await fetch('https://api.cloudinary.com/v1_1/' + cloudName + '/image/upload', { method: 'POST', body });
  const data = await res.json();
  if (data.secure_url) console.log(publicId + ': ' + data.secure_url);
  else console.error(publicId + ' ERROR: ' + JSON.stringify(data));
}

const base = 'D:\\Загрузки Д\\Киммерия Мероприятия\\Пополам\\';
await Promise.all([
  upload(base + 'Обложка.jpg', 'cover'),
  upload(base + 'photo_2026-05-03_20-35-12.jpg', 'photo1'),
  upload(base + 'photo_2026-05-03_20-35-15.jpg', 'photo2'),
  upload(base + 'photo_2026-05-03_20-35-18.jpg', 'photo3'),
  upload(base + 'photo_2026-05-03_20-35-21.jpg', 'photo4'),
  upload(base + 'photo_2026-05-03_20-35-23.jpg', 'photo5'),
]);
