import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
     
      <h1 class="bg-red-500">Vite + React</h1>
      <p className="bg-red-500">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
