/**
 * Signin API Route
 * POST /api/auth/signin
 */

import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";

const AUTH_SECRET = process.env.BETTER_AUTH_SECRET || "hackathon-secret-key-2024";
const SECRET_KEY = new TextEncoder().encode(AUTH_SECRET);

// Access global users store
declare global {
    // eslint-disable-next-line no-var
    var users: Map<string, { id: string; email: string; name: string; password: string }> | undefined;
}

if (!global.users) {
    global.users = new Map();
}

const users = global.users;

async function signToken(payload: { sub: string; email: string; name: string }): Promise<string> {
    return new SignJWT(payload)
        .setProtectedHeader({ alg: "HS256" })
        .setIssuedAt()
        .setExpirationTime("7d")
        .sign(SECRET_KEY);
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { email, password } = body;

        if (!email || !password) {
            return NextResponse.json({ message: "Email and password required" }, { status: 400 });
        }

        const user = users.get(email);

        if (!user || user.password !== password) {
            return NextResponse.json({ message: "Invalid credentials" }, { status: 401 });
        }

        const token = await signToken({ sub: user.id, email: user.email, name: user.name });

        const response = NextResponse.json({
            user: { id: user.id, email: user.email, name: user.name },
            token,
        });

        response.cookies.set("auth_token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 7,
        });

        return response;
    } catch (error) {
        console.error("Signin error:", error);
        return NextResponse.json({ message: "Server error" }, { status: 500 });
    }
}
