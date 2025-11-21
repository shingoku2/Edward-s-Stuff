import React from 'react';

const CornerBrackets = () => (
  <>
    <div className="absolute -top-[1px] -left-[1px] w-12 h-12">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent" />
      <div className="absolute top-0 left-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent" />
      <div className="absolute top-2 left-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute top-2 left-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
    <div className="absolute -top-[1px] -right-[1px] w-12 h-12">
      <div className="absolute top-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent" />
      <div className="absolute top-0 right-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent" />
      <div className="absolute top-2 right-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute top-2 right-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
    <div className="absolute -bottom-[1px] -left-[1px] w-12 h-12">
      <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent" />
      <div className="absolute bottom-0 left-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent" />
      <div className="absolute bottom-2 left-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute bottom-2 left-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
    <div className="absolute -bottom-[1px] -right-[1px] w-12 h-12">
      <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent" />
      <div className="absolute bottom-0 right-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent" />
      <div className="absolute bottom-2 right-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute bottom-2 right-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
  </>
);

export default CornerBrackets;
