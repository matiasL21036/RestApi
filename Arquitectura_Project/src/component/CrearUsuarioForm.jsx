import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function CrearUsuarioForm() {
  const [formData, setFormData] = useState({
    nombre: "",
    rut: "",
    correo: "",
    contrasena: "",
    departamento_id: "", // Relación con el departamento
  });
  const [departamentos, setDepartamentos] = useState([]); // Lista de departamentos
  const navigate = useNavigate();

  // Obtener departamentos desde el backend
  useEffect(() => {
    const fetchDepartamentos = async () => {
      try {
        const { data } = await axios.get("http://localhost:5000/departamentos"); // Eliminado 'response'
        setDepartamentos(data); // Utilizamos 'data' directamente
      } catch (error) {
        console.error("Error al obtener departamentos:", error);
        alert("No se pudieron cargar los departamentos.");
      }
    };
    fetchDepartamentos();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validar los datos antes de enviar
    if (!formData.nombre || !formData.rut || !formData.contrasena) {
      alert("Por favor, complete todos los campos requeridos.");
      return;
    }

    try {
      await axios.post("http://localhost:5000/usuarios_crear", formData); // Eliminado 'response'
      alert("Usuario creado exitosamente");
      setFormData({
        nombre: "",
        rut: "",
        correo: "",
        contrasena: "",
        departamento_id: "",
      });
      navigate("/dashboard"); // Redirigir al dashboard después de crear el usuario
    } catch (error) {
      console.error("Error al crear el usuario:", error);
      if (error.response) {
        alert(error.response.data.error || "Error al crear el usuario.");
      } else {
        alert("Error al conectar con el servidor.");
      }
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Crear Usuario</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Nombre</label>
          <input
            type="text"
            name="nombre"
            value={formData.nombre}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: Juan Pérez"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">RUT</label>
          <input
            type="text"
            name="rut"
            value={formData.rut}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: 12.345.678-9"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Correo (Opcional)</label>
          <input
            type="email"
            name="correo"
            value={formData.correo}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: juan.perez@mail.com"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Contraseña</label>
          <input
            type="password"
            name="contrasena"
            value={formData.contrasena}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">
            Número de Departamento
          </label>
          <select
            name="departamento_id"
            value={formData.departamento_id}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
          >
            <option value="">Seleccione un departamento</option>
            {departamentos.map((departamento) => (
              <option key={departamento.id} value={departamento.id}>
                {departamento.numero_departamento} -{" "}
                {departamento.rut_usuario || "Sin usuario"}
              </option>
            ))}
          </select>
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Crear
          </button>
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}

export default CrearUsuarioForm;
