import { useState, useEffect } from 'react';

function DepartamentoList() {
  const [departamentos, setDepartamentos] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/departamentos')
      .then(response => response.json())
      .then(data => setDepartamentos(data));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold text-blue-600 mb-4">Departamentos</h2>
      <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-md">
        <thead className="bg-blue-600 text-white">
          <tr>
            <th className="py-3 px-4 text-left">Id</th>
            <th className="py-3 px-4 text-left">Número</th>
            <th className="py-3 px-4 text-left">Nombre</th>
            <th className="py-3 px-4 text-left">Tipo</th>
            <th className="py-3 px-4 text-left">Rut Usuario</th>
          </tr>
        </thead>
        <tbody>
          {departamentos.map(depto => (
            <tr key={depto.id} className="border-t hover:bg-gray-100">
              <td className="py-3 px-4">{depto.id}</td>
              <td className="py-3 px-4">{depto.numero_departamento}</td>
              <td className="py-3 px-4">{depto.nombre}</td>
              <td className="py-3 px-4">{depto.tipo_departamento}</td>
              <td className="py-3 px-4">{depto.rut_usuario}</td> 
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DepartamentoList;
