import './App.css'
import Landpage from './component/Landpage'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './component/Dashboard';
import DepartamentoList from './component/DepartamentoList';
import GastoList from './component/GastoList';
import UsuarioList from './component/UsuarioList';
import MarcarComoPagadoForm from './component/MarcarComoPagadoForm';
function App() {
  return (
    <Router>
    <Routes>
      {/* Ruta para la página de inicio (Landpage) */}
      <Route path="/" element={<Landpage />} />
      
      {/* Ruta para el Dashboard */}
      <Route path="/dashboard" element={<Dashboard />} />
      {/* Rutas para los demás componentes */}
      <Route path="/departamentos" element={<DepartamentoList />} />
      <Route path="/gastos" element={<GastoList />} />
      <Route path="/usuarios" element={<UsuarioList />} />
      <Route path="/marcar-como-pagado" element={<MarcarComoPagadoForm />} />
    </Routes>
  </Router>
);
}

export default App;