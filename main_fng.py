"""Punto de entrada principal para el conversor a Forma Normal de Greibach (Microproyecto 2)."""

import sys
from fng.interfaz.ventana_fng import VentanaFNG


def main() -> None:
    """Inicia la aplicación con la interfaz gráfica de usuario para FNG."""
    app = VentanaFNG()
    app.mainloop()


if __name__ == "__main__":
    main()
