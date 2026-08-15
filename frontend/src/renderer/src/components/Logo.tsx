// Logo (wordmark) de l'application, repris du fichier de marque
// vsl/SVG/architecto.svg. Le remplissage utilise `currentColor` pour
// s'adapter au thème (sombre en clair, clair en sombre).

const FONT_FAMILY =
  "'Google Sans Flex 120pt', 'Google Sans Flex', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

export function Logo({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 192.11 40.85"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="architecto"
      fill="currentColor"
    >
      <text
        transform="translate(0 30.03)"
        style={{ fontFamily: FONT_FAMILY, fontSize: 35, fontWeight: 700 }}
      >
        <tspan x="0" y="0">a</tspan>
        <tspan x="20.35" y="0">r</tspan>
        <tspan x="33.91" y="0">chi</tspan>
        <tspan x="84.49" y="0">t</tspan>
        <tspan x="97.49" y="0">e</tspan>
        <tspan x="117.84" y="0">c</tspan>
        <tspan x="137.34" y="0">h</tspan>
        <tspan x="158.25" y="0">t</tspan>
        <tspan x="171.25" y="0">o</tspan>
      </text>
    </svg>
  );
}
