import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function CrearDepartamentoForm() {
  const [formData, setFormData] = useState({
    numero_departamento: "",
    nombre: "",
    tipo_departamento: "",
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (
      !formData.numero_departamento ||
      !formData.nombre ||
      !formData.tipo_departamento
    ) {
      alert("Por favor, complete todos los campos.");
      return;
    }

    try {
      // Realizar la solicitud POST a la API
      await axios.post("http://localhost:5000/departamentos_crear", formData);

      alert("Departamento creado exitosamente");

      // Resetear el formulario
      setFormData({
        numero_departamento: "",
        nombre: "",
        tipo_departamento: "",
      });

      // Redirigir al Dashboard después de crear el departamento
      navigate("/dashboard");
    } catch (error) {
      console.error("Error al crear el departamento:", error);
      if (error.response && error.response.data.error) {
        alert(error.response.data.error);
      } else {
        alert("Error al conectar con el servidor.");
      }
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Crear Departamento</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">
            Número de Departamento
          </label>
          <input
            type="text"
            name="numero_departamento"
            value={formData.numero_departamento}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: 101"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Nombre</label>
          <input
            type="text"
            name="nombre"
            value={formData.nombre}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: Departamento Familiar"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">
            Tipo de Departamento
          </label>
          <input
            type="text"
            name="tipo_departamento"
            value={formData.tipo_departamento}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: Residencial"
          />
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

export default CrearDepartamentoForm;
