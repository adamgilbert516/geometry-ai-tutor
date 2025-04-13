import React, { useEffect, useRef } from 'react';

export default function GeoGebraEmbed({ materialId }) {
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
    <div className="mt-4 border rounded-lg overflow-hidden shadow-sm dark:border-gray-700">
      <div ref={containerRef} id={`ggb-${materialId}`} />
      <div className="p-2 text-center text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800">
        <a
          href={`https://www.geogebra.org/m/${materialId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 underline"
        >
          Open in GeoGebra ↗
        </a>
      </div>
    </div>
  ) : null;
}
