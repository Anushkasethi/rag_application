import React, { useState } from 'react';

const UploadComponent = () => {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    console.log("form data", formData);

    await fetch('http://localhost:8000/upload/', {
    // await fetch('https://rag-application-w3yj.onrender.com/upload/', {
    // await fetch('http://3.80.81.200.nip.io:8000/upload/', {
      method: 'POST',
      body: formData,
      mode: 'no-cors',
    });
  };

  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
};

export default UploadComponent;
