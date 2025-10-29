import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import GestionSilabo from './components/Silabo/Profesor/GestionSilabo';

function App() {
  return (
    <div className="container mt-4"> 
      <h1>Gestión de Sílabo (Vista Profesor)</h1>
      <hr />
      <GestionSilabo /> {/* Muestra tu componente */}
    </div>
  )
}
 

export default App
