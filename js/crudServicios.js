document.addEventListener("DOMContentLoaded", function () {
  const tipoPago = document.getElementById("tipo_pago");
  const recurrencia = document.getElementById("recurrencia");
  const cuotas = document.getElementById("cuotas");

  tipoPago.addEventListener("change", function () {
    if (tipoPago.value === "recurrente") {
      recurrencia.disabled = false;
      recurrencia.required = true;

      cuotas.disabled = true;
      cuotas.required = false;
      cuotas.value = "";
    } else if (tipoPago.value === "pago_unico") {
      cuotas.disabled = false;
      cuotas.required = true;

      recurrencia.disabled = true;
      recurrencia.required = false;
      recurrencia.value = "";
    } else {
      recurrencia.disabled = true;
      cuotas.disabled = true;

      recurrencia.required = false;
      cuotas.required = false;

      recurrencia.value = "";
      cuotas.value = "";
    }
  });
});
