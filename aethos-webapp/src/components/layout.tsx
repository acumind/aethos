"use client";

import React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  SidebarHeader,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import {
  BarChart,
  LineChart,
  PanelLeft,
  Settings,
  User,
  LayoutDashboard,
  Computer
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {useRouter, usePathname} from "next/navigation";
import Link from "next/link";

const navigation = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "User Stats",
    href: "/user-stats",
    icon: User,
  },
  {
    title: "Score Trends",
    href: "/score-trends",
    icon: LineChart,
  },
  {
    title: "Period Analysis",
    href: "/period-analysis",
    icon: BarChart,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
  {
    title: "System",
    href: "/system",
    icon: Computer,
  },
];

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const router = useRouter();
  const pathname = usePathname();

  const breadcrumbs = React.useMemo(() => {
    const pathSegments = pathname.split("/").filter(Boolean);
    const crumbs = [];

    for (let i = 0; i < pathSegments.length; i++) {
      const segment = pathSegments[i];
      const href = "/" + pathSegments.slice(0, i + 1).join("/");
      let title = segment.replace("-", " ").replace(/(.)/, (match) => match.toUpperCase());

      // Special case for agent details page: show the agent name
      if (i === 1 && pathSegments[0] === "system") {
        // Assuming the agent name is the second segment
        title = segment.replace("%20", " "); // Decode URI encoded spaces
      }

      crumbs.push({ href, title });
    }

    return crumbs;
  }, [pathname]);

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <h2 className="font-semibold text-lg tracking-tight">
            Aethos Admin Panel
          </h2>
          <p className="text-muted-foreground">
            Manage and monitor Aethos metrics.
          </p>
        </SidebarHeader>
        <SidebarContent>
          <ScrollArea className="h-[calc(100vh - 8rem)]">
            <SidebarGroup>
              <SidebarGroupLabel>Navigation</SidebarGroupLabel>
              <SidebarMenu>
                {navigation.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton href={item.href}>
                      <item.icon className="mr-2 h-4 w-4" />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroup>
          </ScrollArea>
        </SidebarContent>
        <SidebarFooter>
          <Button variant="outline" className="w-full">
            <PanelLeft className="mr-2 h-4 w-4" />
            Collapse
          </Button>
        </SidebarFooter>
      </Sidebar>
      <div className="md:pl-[16rem] flex-1">
        <div className="container py-10">
          <div className="mb-8">
            <nav aria-label="Breadcrumb">
              <ol className="flex list-none p-0">
                <li>
                  <Link href="/" className="text-blue-500 hover:underline">
                    Dashboard
                  </Link>
                  {breadcrumbs.length > 0 && <span className="mx-2">/</span>}
                </li>
                {breadcrumbs.map((crumb, index) => (
                  <li key={index}>
                    <Link
                      href={crumb.href}
                      className="text-blue-500 hover:underline"
                    >
                      {crumb.title}
                    </Link>
                    {index < breadcrumbs.length - 1 && (
                      <span className="mx-2">/</span>
                    )}
                  </li>
                ))}
              </ol>
            </nav>
          </div>
          {children}
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Layout;
