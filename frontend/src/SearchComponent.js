import React, { useState } from 'react';

const SearchComponent = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState('');

  const handleSearch = async () => {
    const response = await fetch(`http://localhost:8000/search/?query=${query}`);
    // const response = await fetch(`https://rag-application-w3yj.onrender.com/search/?query=${query}`);
    // const response = await fetch(`http://3.80.81.200:8000/search/?query=${query}`);
    const reader = response.body.getReader();
    
    let result = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      result += new TextDecoder().decode(value);
      setResults(result);
    }
  };

  return (
    <div>
      <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleSearch}>Search</button>
      <pre>{results}</pre>
    </div>
  );
};

export default SearchComponent;
