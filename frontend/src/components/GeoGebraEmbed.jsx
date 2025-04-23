import React, { useEffect, useRef } from 'react';

export default function GeoGebraEmbed({ materialId, darkMode }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!materialId || !window.GGBApplet) return;

    const params = {
      appName: "geometry",
      width: "100%",
      height: 400,
      material_id: materialId,
      showToolBar: false,
      showAlgebraInput: false,
    };

    new window.GGBApplet(params, true).inject(containerRef.current.id);

    return () => {
      containerRef.current?.remove();
    };
  }, [materialId]);

  return materialId ? (
    <div className={`mt-4 border rounded-lg overflow-hidden shadow-sm ${darkMode ? "border-gray-700 bg-gray-800" : "border-gray-200 bg-gray-50"}`}>
      <div ref={containerRef} id={`ggb-${materialId}`} />
      <div className={`p-2 text-center text-sm ${darkMode ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-600"}`}>
        <a
          href={`https://www.geogebra.org/m/${materialId}`}
          target="_blank"
          rel="noopener noreferrer"
          className={`underline inline-flex items-center gap-1 ${darkMode ? "text-blue-400 hover:text-blue-300" : "text-blue-600 hover:text-blue-700"}`}
        >
          Explore on GeoGebra ↗
        </a>
      </div>
    </div>
  ) : null;
}
