import React, { useEffect, useState } from 'react';
export function useDebouncing(val, delay) {
  const [debounce, setDebounce] = useState(val);
  useEffect(() => {
    const interval = setTimeout(() => setDebounce(val), delay);

    return () => clearTimeout(interval);
  },[val,delay]);

  return debounce;
}
