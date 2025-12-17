/**
 * Auth API Route - Handles /api/auth/signup and /api/auth/signin
 * 
 * Simple JWT-based auth for hackathon demo.
 */

import { NextRequest, NextResponse } from "next/server";
import { SignJWT, jwtVerify } from "jose";

const AUTH_SECRET = process.env.BETTER_AUTH_SECRET || "hackathon-secret-key-2024";
const SECRET_KEY = new TextEncoder().encode(AUTH_SECRET);

// Simple in-memory store (resets on cold start - fine for demo)
const users = new Map<string, { id: string; email: string; name: string; password: string }>();

async function signToken(payload: { sub: string; email: string; name: string }): Promise<string> {
    return new SignJWT(payload)
        .setProtectedHeader({ alg: "HS256" })
        .setIssuedAt()
        .setExpirationTime("7d")
        .sign(SECRET_KEY);
}

export async function POST(request: NextRequest) {
    const url = new URL(request.url);
    const path = url.pathname;

    console.log("Auth API called:", path);

    try {
        const body = await request.json();
        console.log("Request body:", JSON.stringify(body));

        // SIGNUP
        if (path.endsWith("/signup") || path.includes("/sign-up")) {
            const { email, password, name } = body;

            if (!email || !password) {
                return NextResponse.json({ message: "Email and password required" }, { status: 400 });
            }

            if (users.has(email)) {
                return NextResponse.json({ message: "User already exists" }, { status: 400 });
            }

            const userId = `user_${Date.now()}`;
            users.set(email, { id: userId, email, name: name || email, password });

            const token = await signToken({ sub: userId, email, name: name || email });

            // Store token in cookie
            const response = NextResponse.json({
                user: { id: userId, email, name: name || email },
                token,
            });

            response.cookies.set("auth_token", token, {
                httpOnly: true,
                secure: true,
                sameSite: "lax",
                maxAge: 60 * 60 * 24 * 7, // 7 days
            });

            return response;
        }

        // SIGNIN
        if (path.endsWith("/signin") || path.endsWith("/login") || path.includes("/sign-in")) {
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
                secure: true,
                sameSite: "lax",
                maxAge: 60 * 60 * 24 * 7,
            });

            return response;
        }

        return NextResponse.json({ message: "Not found" }, { status: 404 });

    } catch (error) {
        console.error("Auth error:", error);
        return NextResponse.json({ message: "Server error" }, { status: 500 });
    }
}

export async function GET(request: NextRequest) {
    const url = new URL(request.url);
    const path = url.pathname;

    // SESSION CHECK
    if (path.includes("/session")) {
        const token = request.cookies.get("auth_token")?.value;

        if (!token) {
            return NextResponse.json({ session: null });
        }

        try {
            const { payload } = await jwtVerify(token, SECRET_KEY);
            return NextResponse.json({
                session: {
                    user: { id: payload.sub, email: payload.email, name: payload.name },
                },
            });
        } catch {
            return NextResponse.json({ session: null });
        }
    }

    return NextResponse.json({ status: "ok" });
}
