// import React, { useState } from "react";

// function App() {
//   const [file, setFile] = useState(null);
//   const [query, setQuery] = useState("");
//   const [results, setResults] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const handleFileUpload = async () => {
//     if (!file) return alert("Please select a file.");
//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       await fetch("http://localhost:8000/upload/", {
//         method: "POST",
//         body: formData,
//       });
//       alert("File uploaded successfully!");
//     } catch (error) {
//       alert("Upload failed!");
//     }
//   };

//   const handleSearch = async () => {
//     if (!query) return alert("Enter a search query.");
//     setLoading(true);
//     setResults([]);

//     const response = await fetch(`http://localhost:8000/search/?query=${query}`);
//     const reader = response.body.getReader();

//     let receivedText = "";
//     while (true) {
//       const { done, value } = await reader.read();
//       if (done) break;
//       receivedText += new TextDecoder().decode(value);
//       setResults(receivedText.split("\n"));
//     }
    
//     setLoading(false);
//   };

//   return (
//     <div>
//       <h1>GraphRAG Search</h1>

//       <input type="file" onChange={(e) => setFile(e.target.files[0])} />
//       <button onClick={handleFileUpload}>Upload</button>

//       <input 
//         type="text" 
//         placeholder="Enter search query..." 
//         value={query} 
//         onChange={(e) => setQuery(e.target.value)} 
//       />
//       <button onClick={handleSearch}>Search</button>

//       {loading && <p>Loading...</p>}
//       <div>
//         {results.map((result, index) => (
//           <p key={index}>{result}</p>
//         ))}
//       </div>
//     </div>
//   );
// }

// export default App;
import React, { useState } from "react";
import SearchComponent from "./SearchComponent";
import UploadComponent from "./UploadComponent";

function App() {
  const [results, setResults] = useState([]);

  const handleSearchResults = (data) => {
    setResults(data);
  };

  return (
    <div>
      <h1>GraphRAG Search</h1>
      <UploadComponent />
      <SearchComponent onSearchResults={handleSearchResults} />
      <div>
        {results.map((result, index) => (
          <p key={index}>{result}</p>
        ))}
      </div>
    </div>
  );
}

export default App;