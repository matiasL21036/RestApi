import { useState, useEffect } from 'react';

function GastoList() {
  const [gastos, setGastos] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/gastos_comunes')
      .then(response => response.json())
      .then(data => setGastos(data));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold text-blue-600 mb-4">Gastos Comunes</h2>
      <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-md">
        <thead className="bg-blue-600 text-white">
          <tr>
            <th className="py-3 px-4 text-left">Id</th>
            <th className="py-3 px-4 text-left">Departamento</th>
            <th className="py-3 px-4 text-left">Periodo</th>
            <th className="py-3 px-4 text-left">Monto</th>
            <th className="py-3 px-4 text-left">Pagado</th>
          </tr>
        </thead>
        <tbody>
          {gastos.map(gasto => (
            <tr key={gasto.id} className="border-t hover:bg-gray-100">
              <td className="py-3 px-4">{gasto.id}</td>
              <td className="py-3 px-4">{gasto.departamento_id}</td>
              <td className="py-3 px-4">{gasto.periodo}</td>
              <td className="py-3 px-4">{gasto.monto}</td>
              <td className="py-3 px-4">{gasto.pagado ? 'Sí' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default GastoList;
