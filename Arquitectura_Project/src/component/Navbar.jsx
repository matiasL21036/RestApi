import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav>
      <ul>
        <li><Link to="/departamentos">Departamentos</Link></li>
        <li><Link to="/usuarios">Usuarios</Link></li>
        <li><Link to="/gastos">Gastos</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
