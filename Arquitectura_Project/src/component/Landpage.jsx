import { useState } from 'react';
import axios from 'axios';

const Landpage = () => {
  const [rut, setRut] = useState(''); // Estado para almacenar el RUT ingresado
  const [gastosPendientes, setGastosPendientes] = useState(null); // Estado para los gastos pendientes
  const [error, setError] = useState(''); // Estado para errores

  const handleConsulta = (e) => {
    e.preventDefault();
    setError(''); // Limpiar mensaje de error
    setGastosPendientes(null); // Limpiar datos previos

    // Realizar consulta con el RUT ingresado
    axios
      .get(`http://localhost:5000/api/gastos_pendientes/${rut}`)
      .then((response) => {
        console.log('Datos recibidos:', response.data); // Verifica los datos recibidos

        // Si el backend devuelve un arreglo de gastos
        if (Array.isArray(response.data) && response.data.length > 0) {
          setGastosPendientes(response.data); // Actualiza el estado con los datos
        } else if (response.data.message) {
          // Si la respuesta contiene un mensaje (por ejemplo, "No se encontraron gastos pendientes")
          setError(response.data.message);
        } else {
          setError('No se encontraron gastos pendientes para este RUT');
        }
      })
      .catch((err) => {
        console.log('Error:', err); // Imprime el error en la consola
        if (err.response && err.response.status === 404) {
          setError('No se encontraron gastos pendientes para este RUT');
        } else {
          setError('Ocurrió un error al realizar la consulta');
        }
      });
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h1>Consulta de Gastos Pendientes</h1>
      <form onSubmit={handleConsulta}>
        <label>
          Ingrese su RUT:
          <input
            type="text"
            value={rut}
            onChange={(e) => setRut(e.target.value)}
            placeholder="Ej: 12345678-9"
            required
            style={{ display: 'block', margin: '10px 0', padding: '10px', width: '100%' }}
          />
        </label>
        <button
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          Consultar
        </button>
      </form>

      {/* Mostrar errores */}
      {error && <p style={{ color: 'red', marginTop: '20px' }}>{error}</p>}

      {/* Mostrar resultados */}
      {Array.isArray(gastosPendientes) && gastosPendientes.length > 0 ? (
        <div style={{ marginTop: '20px' }}>
          <h2>Gastos Pendientes</h2>
          <ul>
            {gastosPendientes.map((gasto, index) => (
              <li key={index}>
                <strong>Periodo:</strong> {gasto.periodo} - <strong>Monto:</strong> ${gasto.monto}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        gastosPendientes === null && <p style={{ color: 'blue' }}>Ingrese un RUT para consultar.</p>
      )}
    </div>
  );
};

export default Landpage;
