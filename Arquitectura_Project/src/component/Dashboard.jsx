import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DepartamentoList from './DepartamentoList'; // Para listar departamentos
import UsuarioList from './UsuarioList'; // Para listar usuarios

function Dashboard() {
  const [gastos, setGastos] = useState([]); // Estado para los gastos
  const [filter, setFilter] = useState(''); // Filtrado de gastos por "pagado" o "pendiente"
  const [loadingId, setLoadingId] = useState(null); // Estado de carga específico para cada gasto
  const [error, setError] = useState(null); // Estado para manejar errores

  useEffect(() => {
    fetch('http://localhost:5000/gastos_comunes')
      .then(response => response.json())
      .then(data => setGastos(data))
      .catch(error => {
        setError('Error al obtener los gastos');
        console.error('Error al obtener los gastos:', error);
      });
  }, []);

  const handleFilterChange = (status) => {
    setFilter(status);
  };

  const markAsPaid = (gastoId, departamentoId, anio, mes) => {
    console.log({ gastoId, departamentoId, anio, mes }); // Depuración

    if (!gastoId || !departamentoId || !anio || !mes) {
      console.error("Datos incompletos:", { gastoId, departamentoId, anio, mes });
      alert("Faltan datos para marcar como pagado.");
      return;
    }

    setLoadingId(gastoId); // Mostrar indicador de carga solo para el gasto en proceso
    const data = { departamento_id: departamentoId, anio, mes };

    fetch('http://localhost:5000/marcar_como_pagado', {
      method: 'POST',
      body: JSON.stringify(data),
      headers: { 'Content-Type': 'application/json' },
    })
      .then(response => {
        if (!response.ok) throw new Error('Error en la respuesta del servidor');
        return response.json();
      })
      .then(data => {
        if (data.mensaje === "Pago exitoso") {
          setGastos(prevGastos =>
            prevGastos.map(gasto =>
              gasto.id === gastoId
                ? { ...gasto, pagado: true, fecha_pago: data.fecha_cancelacion }
                : gasto
            )
          );
        } else {
          alert(data.mensaje);
        }
      })
      .catch(error => {
        console.error('Error al marcar como pagado:', error);
        alert('Error al procesar el pago');
      })
      .finally(() => setLoadingId(null)); // Restaurar el estado de carga
  };

  const filteredGastos = gastos.filter(gasto =>
    filter === '' ? true : (gasto.pagado ? 'pagado' : 'pendiente') === filter
  );

  return (
    <div className="min-h-screen bg-gray-100 py-6 px-8">
      <h1 className="text-3xl font-semibold text-center mb-6">Dashboard</h1>

      <div className="mb-6">
        <ul className="flex justify-around space-x-4">
          <li>
            <Link to="/usuarios" className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">Gestionar Usuarios</Link>
          </li>
          <li>
            <Link to="/departamentos" className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition">Gestionar Departamentos</Link>
          </li>
        </ul>
      </div>

      <div className="mb-6 text-center">
        <button onClick={() => handleFilterChange('pagado')} className="bg-blue-500 text-white px-4 py-2 rounded-lg mx-2 hover:bg-blue-600 transition">Mostrar Pagados</button>
        <button onClick={() => handleFilterChange('pendiente')} className="bg-yellow-500 text-white px-4 py-2 rounded-lg mx-2 hover:bg-yellow-600 transition">Mostrar Pendientes</button>
        <button onClick={() => handleFilterChange('')} className="bg-gray-500 text-white px-4 py-2 rounded-lg mx-2 hover:bg-gray-600 transition">Mostrar Todos</button>
      </div>

      <div className="mb-6 overflow-x-auto">
        <h2 className="text-2xl font-medium mb-4">Gastos Comunes</h2>
        {error && <p className="text-red-500">{error}</p>}
        <table className="min-w-full bg-white rounded-lg shadow-md">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2">Id</th>
              <th className="px-4 py-2">Departamento</th>
              <th className="px-4 py-2">Propietario</th>
              <th className="px-4 py-2">Periodo</th>
              <th className="px-4 py-2">Monto</th>
              <th className="px-4 py-2">Pagado</th>
              <th className="px-4 py-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredGastos.map(gasto => (
              <tr key={gasto.id} className="hover:bg-gray-50">
                <td className="px-4 py-2">{gasto.id}</td>
                <td className="px-4 py-2">{gasto.departamento_id}</td>
                <td className="px-4 py-2">{gasto.rut_propietario}</td>
                <td className="px-4 py-2">{gasto.periodo}</td>
                <td className="px-4 py-2">{gasto.monto}</td>
                <td className="px-4 py-2">{gasto.pagado ? 'Sí' : 'No'}</td>
                <td className="px-4 py-2">
                  {!gasto.pagado && gasto.id && gasto.departamento_id && gasto.periodo && (
                    <button
                      onClick={() =>
                        markAsPaid(gasto.id, gasto.departamento_id, new Date(gasto.periodo).getFullYear(), new Date(gasto.periodo).getMonth() + 1)
                      }
                      disabled={loadingId === gasto.id}
                      className={`px-4 py-2 rounded-lg ${
                        loadingId === gasto.id
                          ? 'bg-gray-400 cursor-not-allowed'
                          : 'bg-green-500 text-white hover:bg-green-600'
                      } transition`}
                    >
                      {loadingId === gasto.id ? 'Procesando...' : 'Marcar como Pagado'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <UsuarioList />
      <DepartamentoList />
    </div>
  );
}

export default Dashboard;
