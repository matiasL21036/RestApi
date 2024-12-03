import { useState } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import { useNavigate } from "react-router-dom";  // Importa useNavigate

function MarcarComoPagadoForm({ gasto = {}, }) {
  const [formData, setFormData] = useState({
    departamento_id: gasto.departamento_id || "",
    periodo: gasto.periodo || "",
    monto: gasto.monto || "",
    anio: gasto.periodo ? new Date(gasto.periodo).getFullYear() : "",
    mes: gasto.periodo ? new Date(gasto.periodo).getMonth() + 1 : "",
  });

  const navigate = useNavigate(); // Inicializa el hook para redirección

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    // Asegúrate de que los campos necesarios estén completos
    if (!formData.departamento_id || !formData.anio || !formData.mes) {
      alert("Por favor, complete todos los campos.");
      return;
    }
  
    // Convierte anio y mes a enteros
    const anioInt = parseInt(formData.anio, 10);
    const mesInt = parseInt(formData.mes, 10);
  
    if (isNaN(anioInt) || isNaN(mesInt)) {
      alert("Por favor, ingrese un año y mes válidos.");
      return;
    }
  
    // Verifica los datos antes de enviarlos
    console.log("Datos enviados:", formData);
  
    try {
      // Realiza la solicitud POST a la API con los datos convertidos a números
      const response = await axios.post('http://localhost:5000/marcar_como_pagado', {
        departamento_id: formData.departamento_id,
        anio: anioInt,
        mes: mesInt,
      });
  
      // Verifica la respuesta de la API
      console.log("Respuesta del servidor:", response.data);
  
      // Si la respuesta es exitosa, muestra el mensaje
      alert(response.data.mensaje);

      // Redirige al dashboard después de marcar el gasto como pagado
      navigate("/dashboard"); // Redirige al dashboard o la ruta que desees
    } catch (error) {
      // Verifica el error
      console.error("Error en la solicitud:", error);
  
      if (error.response) {
        // Si hay una respuesta de error desde el servidor
        alert(error.response.data.error);
      } else {
        // Si no hay respuesta (posiblemente un error de red)
        alert("Error al realizar el pago.");
      }
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Marcar Gasto como Pagado</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Departamento ID</label>
          <input
            type="text"
            name="departamento_id"
            value={formData.departamento_id}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Año</label>
          <input
            type="number"
            name="anio"
            value={formData.anio}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Mes</label>
          <input
            type="number"
            name="mes"
            value={formData.mes}
            onChange={handleChange}
            className="w-full p-2 border rounded-lg"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
        >
          Confirmar Pago
        </button>
        <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
          >
            Cancelar
          </button>
      </form>
    </div>
  );
}

MarcarComoPagadoForm.propTypes = {
  gasto: PropTypes.shape({
    departamento_id: PropTypes.string,
    periodo: PropTypes.string,
    monto: PropTypes.number,
  }),
  onCancel: PropTypes.func.isRequired,
};

export default MarcarComoPagadoForm;
