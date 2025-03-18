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
      <h1>RAG Application</h1>
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