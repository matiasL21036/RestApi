import { useState, useEffect } from 'react';

function UsuarioList() {
  const [usuarios, setUsuarios] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/usuarios')
      .then(response => response.json())
      .then(data => setUsuarios(data));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold text-blue-600 mb-4">Usuarios</h2>
      <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-md">
        <thead className="bg-blue-600 text-white">
          <tr>
            <th className="py-3 px-4 text-left">Id</th>
            <th className="py-3 px-4 text-left">Nombre</th>
            <th className="py-3 px-4 text-left">Rut</th>
            <th className="py-3 px-4 text-left">Correo</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map(usuario => (
            <tr key={usuario.id} className="border-t hover:bg-gray-100">
              <td className="py-3 px-4">{usuario.id}</td>
              <td className="py-3 px-4">{usuario.nombre}</td>
              <td className="py-3 px-4">{usuario.rut}</td>
              <td className="py-3 px-4">{usuario.correo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UsuarioList;
