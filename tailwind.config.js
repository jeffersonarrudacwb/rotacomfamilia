/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./*.html'],
  theme: {
    extend: {
      colors: {
        brand: {
          deep:   '#14150D',
          navy:   '#1F2014',
          blue:   '#2A2B19',
          leaf:   '#7A8A5F',
          fern:   '#A9B47E',
          sky:    '#F4E4C1',
          azure:  '#E3B04B',
          orange: '#D4A437',
          flame:  '#C8732E',
          cream:  '#FAF1DA',
        },
      },
      fontFamily: {
        // Duas familias carregadas: Playfair Display (titulos) e Inter (corpo).
        //
        // 'display' e 'serif' apontam ambos para Playfair porque as paginas
        // usam nomes diferentes para a mesma intencao: o index.html marca
        // titulos com font-display, e as demais paginas com font-serif.
        // Unificar aqui evita ter de reescrever 62 ocorrencias no HTML.
        //
        // Plus Jakarta Sans saiu: era so o corpo de texto do index.html, e o
        // Inter cobre esse papel.
        //
        // A stack monoespacada do sistema tambem saiu. Ela nao custava
        // download, mas resolvia para uma fonte diferente em cada sistema
        // (Consolas no Windows, SF Mono no Mac, Roboto Mono no Android), entao
        // os rotulos e numeros do site apareciam com um tipo que ninguem
        // escolheu e que nao combina com a identidade. Onde a intencao era
        // alinhar numeros, o que resolve e font-variant-numeric: tabular-nums
        // no Inter, aplicado direto no styles.css.
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        serif:   ['"Playfair Display"', 'Georgia', 'serif'],
        sans:    ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        soft:  '0 24px 50px -20px rgba(0,0,0,0.55)',
        glow:  '0 10px 30px -10px rgba(212,164,55,0.55)',
      },
    },
  },
  plugins: [],
}
