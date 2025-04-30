"use client";
import {
    Menubar,
    MenubarContent,
    MenubarItem,
    MenubarMenu,
    MenubarTrigger,
} from "@/components/ui/menubar"
import {Avatar, AvatarFallback, AvatarImage} from "@/components/ui/avatar";

export function Navbar() {
    return (
        <div className="flex justify-between items-center p-4 shadow-md" style={{ backgroundColor: 'hsl(var(--navbar-background))', color: 'hsl(var(--navbar-foreground))' }}>
            <div className="flex items-center space-x-4">
                <Avatar>
                    <AvatarImage src="https://picsum.photos/50/50" alt="Avatar"/>
                    <AvatarFallback>RAI</AvatarFallback>
                </Avatar>
                <h1 className="text-xl font-bold">Aethos Client</h1>
            </div>
            <div>
                <Menubar>
                    <MenubarMenu>
                        <MenubarTrigger>Settings</MenubarTrigger>
                        <MenubarContent>
                            <MenubarItem>Profile</MenubarItem>
                            <MenubarItem>Preferences</MenubarItem>
                            <MenubarItem>Logout</MenubarItem>
                        </MenubarContent>
                    </MenubarMenu>
                </Menubar>
            </div>
        </div>
    );
}
