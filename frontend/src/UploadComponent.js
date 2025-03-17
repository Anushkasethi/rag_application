import React, { useState } from 'react';

const UploadComponent = () => {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    // await fetch('http://localhost:8000/upload/', {
    await fetch('https://rag-application-w3yj.onrender.com/upload/', {
      method: 'POST',
      body: formData
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
