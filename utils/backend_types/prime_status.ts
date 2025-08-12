export type PrimePart = {
    parts: string;
    id: number;
};

export type PrimeSet = {
    warframe_set: string;
    status: string;
    type: string;
    parts: PrimePart[];
};

export type PrimeStatusResponse = PrimeSet[];
