// Formatea un valor en pesos colombianos: sin decimales y con punto de miles.
export function formatearPrecio(valor) {
  const entero = Math.round(valor).toString()
  const conPuntos = entero.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  return '$ ' + conPuntos
}
