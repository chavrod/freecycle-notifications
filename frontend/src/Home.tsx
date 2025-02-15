export default function Home() {
  const colors = [
    "#c4d5bf",
    "#b6dbb8",
    "#a0ceaf",
    "#a3d6c7",
    "#75b1a7",
    "#5fa08a",
    "#498f6e",
    "#326950",
    "#1c5242",
    "#053c34",
  ];
  return (
    <div>
      <h1>Welcome</h1>

      <p>Welcome to the React ❤️ django-allauth.</p>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          marginTop: "20px",
        }}
      >
        {colors.map((color, index) => (
          <div
            key={index}
            style={{ backgroundColor: color, height: "50px", width: "100px" }}
          >
            {color}
          </div>
        ))}
      </div>
    </div>
  );
}
