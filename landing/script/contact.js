// Contato: links do WhatsApp e formulário (WhatsApp + planilha do Google)
(() => {
  function buildWhatsappUrl(text) {
    return `https://wa.me/${SITE_CONFIG.whatsappNumber}?text=${encodeURIComponent(text)}`;
  }

  // Links com data-whatsapp apontam para o número da empresa
  document.querySelectorAll("[data-whatsapp]").forEach((link) => {
    link.href = buildWhatsappUrl(link.dataset.whatsappText ?? "");
  });

  // Máscara (99) 99999-9999
  function formatPhone(value) {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    if (digits.length <= 2) return digits ? `(${digits}` : "";
    if (digits.length <= 7) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  }

  const phoneInput = document.getElementById("telephone");
  phoneInput.addEventListener("input", () => {
    phoneInput.value = formatPhone(phoneInput.value);
  });

  function showFormStatus(message, isError = false) {
    const status = document.getElementById("form-status");
    status.textContent = message;
    status.classList.toggle("form-status--error", isError);
  }

  function buildLeadMessage(lead) {
    return [
      `Olá! Meu nome é ${lead.name}.`,
      `Cidade/UF: ${lead.city} - ${lead.uf}`,
      `Telefone: ${lead.phone}`,
      `Email: ${lead.email}`,
      "",
      lead.message,
    ].join("\n");
  }

  const contactForm = document.getElementById("contact-form");

  // O botão só é liberado com o consentimento marcado
  const consentCheckbox = contactForm.elements.consent;
  const submitButton = contactForm.querySelector("button[type=submit]");

  function syncSubmitButton() {
    submitButton.disabled = !consentCheckbox.checked;
  }

  consentCheckbox.addEventListener("change", syncSubmitButton);
  contactForm.addEventListener("reset", () => setTimeout(syncSubmitButton));
  syncSubmitButton();

  contactForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const form = contactForm.elements;

    // Honeypot preenchido = bot; descarta em silêncio
    if (form.website.value) return;

    const lead = {
      name: form.firstName.value.trim(),
      email: form.mail.value.trim(),
      city: form.city.value.trim(),
      uf: form.uf.value,
      phone: form.phone.value.trim(),
      message: form.menssage.value.trim(),
    };

    // Registra na planilha sem aguardar a resposta (text/plain evita preflight de CORS)
    if (SITE_CONFIG.sheetsEndpoint) {
      fetch(SITE_CONFIG.sheetsEndpoint, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify(lead),
        keepalive: true,
      }).catch(() => {});
    }

    // Abre o WhatsApp no próprio clique (evita bloqueio de pop-up no iOS)
    const whatsappWindow = window.open(buildWhatsappUrl(buildLeadMessage(lead)), "_blank");
    if (!whatsappWindow) {
      window.location.href = buildWhatsappUrl(buildLeadMessage(lead));
    }

    contactForm.reset();
    showFormStatus("Recebemos seus dados! Continue o atendimento pelo WhatsApp.");
  });
})();
