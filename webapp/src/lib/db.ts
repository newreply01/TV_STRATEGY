import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres123@localhost:5433/tradeview_strategy?schema=public',
});

export const query = (text: string, params?: any[]) => pool.query(text, params);

export default pool;
