import { useGLTF } from '@react-three/drei';

// Model paths - these can be replaced with actual GLTF files
export const MODEL_PATHS = {
  characters: {
    worker: '/models/characters/office-worker.glb',
  },
  furniture: {
    desk: '/models/furniture/desk.glb',
    chair: '/models/furniture/chair.glb',
    computer: '/models/furniture/computer.glb',
    plant: '/models/furniture/plant.glb',
  },
  environment: {
    officeFloor: '/models/environment/office-floor.glb',
  },
};

// Preload all models - call this when the app starts
export const preloadModels = () => {
  const allPaths = [
    ...Object.values(MODEL_PATHS.characters),
    ...Object.values(MODEL_PATHS.furniture),
    ...Object.values(MODEL_PATHS.environment),
  ];

  allPaths.forEach((path) => {
    useGLTF.preload(path);
  });
};

// Check if a model file exists
export const checkModelExists = async (path: string): Promise<boolean> => {
  try {
    const response = await fetch(path, { method: 'HEAD' });
    return response.ok;
  } catch {
    return false;
  }
};
