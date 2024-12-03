import { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Landpage = () => {
  const [rut, setRut] = useState('');
  const [gastosPendientes, setGastosPendientes] = useState(null);
  const [error, setError] = useState('');

  const handleConsulta = (e) => {
    e.preventDefault();
    setError('');
    setGastosPendientes(null);

    axios
      .get(`http://localhost:5000/api/gastos_pendientes/${rut}`)
      .then((response) => {
        if (Array.isArray(response.data) && response.data.length > 0) {
          setGastosPendientes(response.data);
        } else if (response.data.message) {
          setError(response.data.message);
        } else {
          setError('No se encontraron gastos pendientes para este RUT');
        }
      })
      .catch((err) => {
        if (err.response && err.response.status === 404) {
          setError('No se encontraron gastos pendientes para este RUT');
        } else {
          setError('Ocurrió un error al realizar la consulta');
        }
      });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <nav className="bg-blue-600 text-white py-4">
        <div className="container mx-auto flex justify-between items-center px-6">
          <h1 className="text-2xl font-bold">Sistema de Gastos Comunes</h1>
          <Link
            to="/dashboard"
            className="ml-6 bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
          >
            Ir al Dashboard
          </Link>
        </div>
      </nav>

      {/* Formulario */}
      <div className="container mx-auto py-8 px-6">
        <h2 className="text-3xl font-semibold text-center mb-6">Consulta de Gastos Pendientes</h2>
        <form
          onSubmit={handleConsulta}
          className="bg-white p-6 rounded-lg shadow-md max-w-lg mx-auto"
        >
          <label className="block text-lg font-medium mb-2">
            Ingrese su RUT:
            <input
              type="text"
              value={rut}
              onChange={(e) => setRut(e.target.value)}
              placeholder="Ej: 12.345.678-9"
              required
              className="w-full px-4 py-2 border rounded-lg mt-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg mt-4 hover:bg-blue-700 transition"
          >
            Consultar
          </button>
        </form>

        {/* Mostrar errores */}
        {error && <p className="text-red-500 text-center mt-4">{error}</p>}

        {/* Mostrar resultados */}
        {Array.isArray(gastosPendientes) && gastosPendientes.length > 0 && (
          <div className="mt-6 bg-white p-6 rounded-lg shadow-md max-w-lg mx-auto">
            <h3 className="text-xl font-semibold mb-4">Gastos Pendientes</h3>
            <ul className="space-y-2">
              {gastosPendientes.map((gasto, index) => (
                <li key={index} className="border-b pb-2">
                  <strong>Periodo:</strong> {gasto.periodo} -{' '}
                  <strong>Monto:</strong> ${gasto.monto}
                </li>
              ))}
            </ul>
          </div>
        )}

        {!gastosPendientes && !error && (
          <p className="text-blue-500 text-center mt-4">
            Ingrese un RUT para consultar.
          </p>
        )}
      </div>
    </div>
  );
};

export default Landpage;
