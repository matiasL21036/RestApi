import { useState } from "react";
import axios from "axios";

function GenerarGastosForm() {
  const [anio, setAnio] = useState("");
  const [mes, setMes] = useState(""); // Mes opcional
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  const handleAnioChange = (e) => setAnio(e.target.value);
  const handleMesChange = (e) => setMes(e.target.value);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validación de los campos
    if (!anio) {
      setError("El año es obligatorio.");
      return;
    }
    if (mes && (mes < 1 || mes > 12)) {
      setError("El mes debe estar entre 1 y 12.");
      return;
    }

    try {
      await axios.post("http://localhost:5000/generar_gastos", {
        anio,
        mes: mes ? parseInt(mes) : null, // Si el mes no es proporcionado, se pasa como null
      });

      setMensaje("Gastos generados exitosamente.");
      setError(null); // Limpiar el mensaje de error
    } catch (err) {
      console.error("Error al generar los gastos:", err);
      setError("Hubo un error al generar los gastos. Intenta nuevamente.");
      setMensaje(null); // Limpiar el mensaje de éxito
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Generar Gastos Comunes</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Año</label>
          <input
            type="number"
            value={anio}
            onChange={handleAnioChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: 2024"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Mes (Opcional)</label>
          <input
            type="number"
            value={mes}
            onChange={handleMesChange}
            className="w-full p-2 border rounded-lg"
            placeholder="Ejemplo: 5 (para mayo)"
            min="1"
            max="12"
          />
        </div>

        {error && <div className="text-red-500 text-sm">{error}</div>}
        {mensaje && <div className="text-green-500 text-sm">{mensaje}</div>}

        <div className="flex space-x-4">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Generar Gastos
          </button>
        </div>
      </form>
    </div>
  );
}

export default GenerarGastosForm;
